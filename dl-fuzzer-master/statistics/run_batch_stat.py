import argparse
import os
import glob
import shutil
import csv
import pandas as pd

def check_dir_exist(d):
    d = os.path.abspath(d)
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError("%s is not a valid work directory" % d)
    return d

def verify_workdir(inputs_dir_list, yamls_list):
  input_dirs_counter = 0
  for yaml_workdir in inputs_dir_list:
    if not os.path.isdir(yaml_workdir):
      continue
    os.chdir(yaml_workdir)  
    pCounter = len(glob.glob1(os.getcwd(),"*.p"))

    if pCounter > 0:
      yaml_fname = yaml_workdir[:-len('_workdir')]
      if yaml_fname in yamls_list:
          input_dirs_counter += 1
          os.chdir('..')
      else:
        print("======== W A R N ======== NO valid yaml file to fuzz for %s." % (yaml_fname))
        os.chdir('..')
        #shutil.rmtree(yaml_workdir)

    else:
      print("======== W A R N ======== %s has no *.p files." % (yaml_workdir))
      os.chdir('..')
      #os.rmdir(yaml_workdir)
  
  print ('\u00B7\u00B7\u00B7\u00B7 Inputs were created from %d valid yaml files' % (input_dirs_counter)) #\u00B7 indicates the unicode for a middle dot

def retreive_common_info(input_dir):
  out_list = []
  out_log = input_dir + "/out"
  if os.path.exists(out_log):
    timeout_occur = 0
    with open(out_log, 'r') as f:
      for line in f.readlines():
        if 'Warning: Process Timed Out' in line:
          timeout_occur += 1
    out_list.append(timeout_occur)
  else:
    out_list.append("N/A")
  pCounter = len(glob.glob1(input_dir,"*.p"))
  #print ("%s : %s" % (input_dir, pCounter))
  eCounter = len(glob.glob1(input_dir,"*.e"))
  cCounter = len(glob.glob1(input_dir,"cluster_*"))
  ratio = 'N/A'
  if pCounter > 0:
    ratio = round((eCounter / pCounter), 2)
  out_list.append(pCounter)
  out_list.append(eCounter)
  out_list.append(ratio)
  out_list.append(cCounter)
  return out_list

def run_permute(input_dir_list, csv_out):
  print ("==== Analyzing inputs for permute ====")
  with open(csv_out, mode='w') as outfile:
    csv_writer = csv.writer(outfile)
    # Writing header
    csv_writer.writerow(['API', '# timeout', '# inputs', '# exceptions', 'exception ratio', '# clusters', '# dtype permutes', '# valid permutes', 'valid permute ratio'])
        
    for yaml_workdir in input_dir_list:
      if not os.path.isdir(yaml_workdir):
        continue
      api_name = yaml_workdir[:-len('.yaml_workdir')]
      row = retreive_common_info(yaml_workdir)
      row.insert(0, api_name)

      permute_file = yaml_workdir + '/dtype_permute' 
      if (os.path.exists(permute_file)):
        pCounter = 0 #permute counter
        vpCounter = 0 #valud permute counter
        with open(permute_file) as f:
          for line in f:
              pCounter += 1
              if "=> Yes" in line:
                vpCounter += 1
        row.append(pCounter)
        row.append(vpCounter)
        ratio = round((vpCounter / pCounter), 2)
        row.append(ratio)
        csv_writer.writerow(row)
      else:
        print ("%s does not exist. Not including dtype info in CSV output." % permute_file)
        row.append("N/A")
        row.append("N/A")
        csv_writer.writerow(row)
      

  

def run_prev_ok(input_dir_list, csv_out):
  print ("==== Analyzing inputs for prev_ok ====")
  with open(csv_out, mode='w') as outfile:
    csv_writer = csv.writer(outfile)
    # Writing header
    csv_writer.writerow(['API', '# timeout', '# inputs', '# exceptions', 'exception ratio', '# clusters'])
    
    for yaml_workdir in input_dir_list:
      if not os.path.isdir(yaml_workdir):
        continue
      api_name = yaml_workdir[:-len('.yaml_workdir')]
      row = retreive_common_info(yaml_workdir)
      row.insert(0, api_name)
      csv_writer.writerow(row)

def averageCsvColumns(csv_out):
  data = pd.read_csv(csv_out)
  all_cols_mean = data.mean(axis=0).round(2).tolist()  #get means for all columns
  all_cols_mean.insert(0, 'Average')
  with open(csv_out, 'a+') as outfile: #append means at the bottom
    csv_writer = csv.writer(outfile)
    csv_writer.writerow(all_cols_mean)
  

def main(workdir, yamlstofuzz, csv_out):
  print ("==== Verifying folders in workdir ====")
  input_dirs = sorted(os.listdir(workdir))
  verify_workdir(input_dirs, os.listdir(yamlstofuzz))

  if "permute" in workdir: 
    run_permute(input_dirs, csv_out)
  elif "prev_ok" in workdir:
    run_prev_ok(input_dirs, csv_out)
  else:
    print ("======== E R R O R ========\"--workdir\" should contain either \"permute\" or \"prev_ok\" in its name. Exiting...")
    exit(1)
  
  averageCsvColumns(csv_out)


if __name__== '__main__':
  parser=argparse.ArgumentParser()
  parser.add_argument('--workdir', type=check_dir_exist, required=True, help='Work directory that stores fuzzing output. E.g., /.../.workdir/expect_ok_permute')
  parser.add_argument('--yamldir', type=check_dir_exist, default='../constraints/constraint_1/changed', help='Directory that stores yaml files for fuzzing. If not provided, it is given "../constraints/constraint_1/changed/"')
  parser.add_argument('--output', default=os.getcwd() + '/fuzzing_stats.csv', help='Path to CSV file for statistics output. If not provided, it is written to fuzzing_stats.csv in the current directory.')
  args = parser.parse_args()
  workdir = args.workdir
  yamldir = args.yamldir
  csv_out = args.output

  os.chdir(workdir)
  main(workdir, yamldir, csv_out)
