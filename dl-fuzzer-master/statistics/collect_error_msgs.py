import argparse
import os
import csv
import glob
import pandas as pd

def check_dir_exist(d):
  d = os.path.abspath(d)
  if not os.path.isdir(d):
    raise argparse.ArgumentTypeError("%s is not a valid work directory" % d)
  return d

def extractTime(log_file):
  result = "N/A"
  if os.path.exists(log_file):
    with open(log_file, 'r') as f:
      result = f.readline().split()[0] #extract only number from 125.70
  return result

def retreive_common_info(input_dir):
  out_list = []
  out_log = input_dir + "/out"
  timeout_script = input_dir + "/timeout_script_record"
  failure_script = input_dir + "/failure_script_record" 
  script_record_occur = 0
  timeout_occur = 0
  failure_occur = 0
  signal_occur = 0
  if os.path.exists(out_log):
    if os.path.exists(timeout_script):
      timeout_occur = len(open(timeout_script).readlines()) 
    if os.path.exists(failure_script):
#      print ("failure_script: %s" % failure_script)
      failure_occur = len(open(failure_script).readlines()) 
    out_list.append(timeout_occur)

    script_record_list = glob.glob(input_dir + '/*_script_record')
#    print ("script_record_list: %s" % script_record_list) 
    if len(script_record_list) > 0:
      for file_name in script_record_list:
        with open(file_name, 'r') as f:
          if file_name != failure_script:
            script_record_occur += len(open(file_name).readlines()) 
#            print ("script_record_occur: %s %s" % (file_name, script_record_occur))
      signal_occur = script_record_occur -  timeout_occur
    out_list.append(signal_occur)
  else:
    out_list.append("N/A")
    out_list.append("N/A")

  pCounter = len(glob.glob1(input_dir,"*.p"))
  #print ("%s : %s" % (input_dir, pCounter))
  eCounter = len(glob.glob1(input_dir,"*.e"))
  cCounter = len(glob.glob1(input_dir,"cluster_[0-9]*"))
  if eCounter == 1:
    cCounter = 1
  if pCounter > 0:
    if "exception" in workdir: 
      ratio = 1 - round((failure_occur / pCounter), 2)
    else:
      ratio = 1 - round(((failure_occur + signal_occur + timeout_occur) / pCounter), 2)
  else:
    ratio = "N/A"
  # clusters
  out_list.append(cCounter)
  # valid ratio
  out_list.append(ratio)
  # generated inputs
  out_list.append(pCounter)
  # valid inputs
  if "exception" in workdir: 
    out_list.append(pCounter - failure_occur)
  else:
    out_list.append(pCounter - (failure_occur + signal_occur + timeout_occur))
  # running time
  runningtime = extractTime(input_dir + "/fuzz_time")
  if runningtime != "N/A":
    runningtime = float(runningtime)
  out_list.append(runningtime)
  # clustering time
  clusteringtime = extractTime(input_dir + "/cluster_time")
  if clusteringtime != "N/A":
    clusteringtime = float(clusteringtime)
  out_list.append(clusteringtime)  

  return out_list

def retreive_error_msg(input_dir):
  print("---- Collecting error msgs for %s ---- " % input_dir)
  cluster_msgs = []
  cluster_files = []
  eCounter = len(glob.glob1(input_dir,"*.e"))
  if eCounter == 1:
    cluster_files = sorted(glob.glob1(input_dir, "*.e"))
  else:
    cluster_files = sorted(glob.glob1(input_dir, "cluster_[0-9]*"))
  if len(cluster_files) == 0:
    return "N/A - no exception"
  
  n = 5 #output error msgs only up to 5 clusters due to space
  for c in cluster_files:
    if n <= 0:
      break
    n -= 1
    with open(input_dir +"/" + c) as f:
      first_efile = f.readline().rstrip('\n')
      if c.endswith(".e"):
        cluster_msgs.append("* " + first_efile)
        continue
      with open(input_dir + '/' + first_efile, "r") as efile:
        e_data = efile.readline().rstrip('\n')
        cluster_msgs.append("* " + e_data)

  return '\n'.join(cluster_msgs)

def run_permute(input_dirs, csv_out):
  count = 0
  with open(csv_out, mode='w') as outfile:
    csv_writer = csv.writer(outfile)
    # Writing header
    csv_writer.writerow(['API', 'Error messages', '# timeout', '# signal', '# clusters', 'exception ratio', '# inputs', '# exceptions', 'fuzzing time', 'clustering time', '# dtype permutes', '# valid permutes', 'valid permute ratio'])
    for yaml_workdir in input_dirs:
      if not os.path.isdir(yaml_workdir):
        continue
#      eCounter = len(glob.glob1(yaml_workdir,"*.e"))
#      if eCounter <= 0:
#        continue
      api_name = yaml_workdir[:-len('.yaml_workdir')]
      row = retreive_common_info(yaml_workdir)
      row.insert(0, api_name)
      error_msg = retreive_error_msg(yaml_workdir)
      row.insert(1, error_msg)

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
      else:
        print ("%s does not exist. Not including dtype info in CSV output." % permute_file)
        row.append("N/A")
        row.append("N/A")
        row.append("N/A")

      csv_writer.writerow(row)
      count += 1
  print ("Upto 5 error messages have been written for %s APIs to %s" % (count, csv_out))

def run_prev_ok(input_dirs, csv_out):
  count = 0
  with open(csv_out, mode='w') as outfile:
    csv_writer = csv.writer(outfile)
    # Writing header
    csv_writer.writerow(['API', 'Error messages', '# timeout', '# signal', '# clusters', 'valid ratio', '# inputs', '# valid', 'fuzzing time', 'clustering time'])
    for yaml_workdir in input_dirs:
      if not os.path.isdir(yaml_workdir):
        continue
#      eCounter = len(glob.glob1(yaml_workdir,"*.e"))
#      if eCounter <= 0:
#        continue
      api_name = yaml_workdir[:-len('.yaml_workdir')]
      row = retreive_common_info(yaml_workdir)
      row.insert(0, api_name)
      if ".v1." in yaml_workdir or "division" in yaml_workdir: # to filter out TF v1
        continue
      error_msg = retreive_error_msg(yaml_workdir)
      row.insert(1, error_msg)
      csv_writer.writerow(row)
      count += 1
  print ("Upto 5 error messages have been written for %s APIs to %s" % (count, csv_out))

def averageCsvColumns(csv_out):
  data = pd.read_csv(csv_out)
  data = data.loc[:, data.columns != 'API'] #exclude first column
  data = data.loc[:, data.columns != 'Error messages'] #exclude second column
  #min
  mini = data.min(axis=0).tolist()
  mini.insert(0, 'Min')
  mini.insert(1, 'N/A') 
  #max
  maxi = data.max(axis=0).tolist()
  maxi.insert(0, 'Max')
  maxi.insert(1, 'N/A') 
  #median
  median = data.median(axis=0).round(2).tolist()  
  median.insert(0, 'Median')
  median.insert(1, 'N/A') 
  #mean
  mean = data.mean(axis=0).round(2).tolist()  #get means for all columns (axis=0 is column, 1 is row)
  mean.insert(0, 'Average')
  mean.insert(1, 'N/A') # can't get average of error messages
  #sum
  summ = data.sum(axis=0).round(2).tolist()  
  summ.insert(0, 'Sum')
  summ.insert(1, 'N/A') 

  with open(csv_out, 'a+') as outfile: #append means at the bottom
    csv_writer = csv.writer(outfile)
    csv_writer.writerow(mini)
    csv_writer.writerow(maxi)
    csv_writer.writerow(median)
    csv_writer.writerow(mean)
    csv_writer.writerow(summ)
 
def main(input_dirs, csv_out):
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
  parser.add_argument('--output', default=os.getcwd() + '/error_msgs.csv', help='Absolute path to CSV file for error messages output. If not provided, it is written to error_msgs.csv in the current directory.')
  args = parser.parse_args()
  workdir = args.workdir
  csv_out = args.output

  os.chdir(workdir)
  main(sorted(os.listdir(workdir)), csv_out)
