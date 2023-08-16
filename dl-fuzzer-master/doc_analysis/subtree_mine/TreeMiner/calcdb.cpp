#include <iostream>
#include "calcdb.h"
#include "treeminer.h"

int *Dbase_Ctrl_Blk::FreqIdx=NULL;
int *Dbase_Ctrl_Blk::FreqMap=NULL;
int Dbase_Ctrl_Blk::MaxTransSz=0;
int Dbase_Ctrl_Blk::TransSz=0;
int *Dbase_Ctrl_Blk::TransAry=NULL;
int Dbase_Ctrl_Blk::Tid=0;
int Dbase_Ctrl_Blk::Cid=0;
int Dbase_Ctrl_Blk::NumF1=0;
int *Dbase_Ctrl_Blk::PvtTransAry=NULL;
//vector<idlist> Dbase_Ctrl_Blk::Idlists;
bool Dbase_Ctrl_Blk::binary_input=false;

Dbase_Ctrl_Blk::Dbase_Ctrl_Blk(const char *infile, const int buf_sz)
{
   if (binary_input){
      fd.open(infile, ios::in|ios::binary);
      if (!fd){
         cerr << "cannot open infile" << infile << endl;
         exit(1);
      }
   }
   else{
      fd.open(infile, ios::in);
      if (!fd){
         cerr << "cannot open infile" << infile << endl;
         exit(1);
      }
   }
   
   buf_size = buf_sz;
   buf = new int [buf_sz];
   cur_buf_pos = 0;
   cur_blk_size = 0;
   readall = 0;
   fd.seekg(0,ios::end);
   endpos = fd.tellg();
   fd.seekg(0,ios::beg);
}
   
Dbase_Ctrl_Blk::~Dbase_Ctrl_Blk()
{
   delete [] buf;
   fd.close();
}

void Dbase_Ctrl_Blk::get_first_blk()
{
   readall=0;

   fd.clear();
   fd.seekg(0,ios::beg);
   
   if (binary_input){
      fd.read((char *)buf, (buf_size*ITSZ));
      cur_blk_size = fd.gcount()/ITSZ; 
      if (cur_blk_size < 0){
         cerr << "problem in get_first_blk" << cur_blk_size << endl;
      }
      if (cur_blk_size < buf_size){
         fd.clear();
         fd.seekg(0,ios::end);
      }
   }
   
   cur_buf_pos = 0;
}

int Dbase_Ctrl_Blk::get_next_trans ()
{
   static char first=1;  

   if (first){
      first = 0;
      get_first_blk();
   }

   if (binary_input){
      if (cur_buf_pos+TRANSOFF >= cur_blk_size ||
          cur_buf_pos+buf[cur_buf_pos+TRANSOFF-1]+TRANSOFF > cur_blk_size){
         fd.seekg(0,ios::cur);
         if (((int)fd.tellg()) == endpos) readall = 1;      
         if (!readall){
            // Need to get more items from file
            get_next_trans_ext();
         }      
      }
      
      if (eof()){
         first = 1;
         return 0;
      }                     
      
      if (!readall){
         Cid = buf[cur_buf_pos];
         Tid = buf[cur_buf_pos+TRANSOFF-2];
         TransSz = buf[cur_buf_pos+TRANSOFF-1];
         TransAry = buf + cur_buf_pos + TRANSOFF;
         cur_buf_pos += TransSz + TRANSOFF;
      }
      return 1;
   }
   else{
      //fd.seekg(0,ios::cur);
      //if (fd.tellg() == endpos) readall = 1;

      if ((int)fd.tellg() == endpos-1){
         readall = 1;
         first = 1;
         return 0;
      }
      else{
         int i;
         fd >> Cid;
         fd >> Tid;
         fd >> TransSz;
         for (i=0; i < TransSz; ++i){
            fd >> buf[i];
         }
         TransAry = buf;
         cur_buf_pos = 0;

         //cout << "ENDPOS " << fd.tellg() << " " << endpos << endl;

         return 1;
      }
   }
   
}

void Dbase_Ctrl_Blk::get_next_trans_ext()
{
   // Need to get more items from file
   int res = cur_blk_size - cur_buf_pos;
   if (res > 0)
   {
      // First copy partial transaction to beginning of buffer
      for (int i=0; i < res; i++)
         buf[i] = buf[cur_buf_pos+i]; 
      cur_blk_size = res;
   }
   else
   {
      // No partial transaction in buffer
      cur_blk_size = 0;
   }

   fd.read((char *)(buf + cur_blk_size),
           ((buf_size - cur_blk_size)*ITSZ));
   
   res = fd.gcount();
   if (res < 0){
      cerr << "in get_next_trans_ext" << res << endl;
   }

  if (res < (buf_size - cur_blk_size)){
      fd.clear();
      fd.seekg(0,ios::end);
   }

   
   cur_blk_size += res/ITSZ;
   cur_buf_pos = 0;
}


void Dbase_Ctrl_Blk::get_valid_trans()
{
   int i,j;
   const int invalid=-3; //-3 does not appear in original trans
   
   if (PvtTransAry == NULL)
      PvtTransAry = new int [MaxTransSz];
   
   //remove infreq items
   //cout << "ORIG " << endl;
   //for (i=0; i < TransSz; i++)
   //   cout << TransAry[i] << " ";
   //cout << endl;
   //cout << "ORIGV " << endl;
   //for (i=0; i < TransSz; i++)
   //   if (TransAry[i] != -1 && theFreqMap[TransAry[i]] == -1)
   //      cout << "-3 ";
   //   else   cout << TransAry[i] << " ";
   //cout << endl;
   

   for (i=0; i < TransSz; i++){      
      if (TransAry[i] != invalid){
         if (TransAry[i] != BranchIt){   
            if (FreqMap[TransAry[i]] == -1){
               //set item to invalid and the next -1 to invalid
               TransAry[i] = invalid;
               int cnt=0;
               
               for(j=i+1; j < TransSz && cnt >= 0; j++){
                  if (TransAry[j] != invalid){
                     if (TransAry[j] == BranchIt) cnt--;
                     else cnt++;
                  }
               }
               TransAry[--j] = invalid;
            }
         }
      }
   }
   
   //cout << "VALID " << endl;
   //for (i=0; i < TransSz; i++)
   //   cout << TransAry[i] << " ";
   //cout << endl;

   //copy valid items to PvtTransAry
   for (i=0,j=0; i < TransSz; i++){
      if (TransAry[i] != invalid){
         if (TransAry[i] == BranchIt) PvtTransAry[j] = TransAry[i];
         else PvtTransAry[j] = FreqMap[TransAry[i]];
         j++;
      }
   }
   TransAry = PvtTransAry;
   TransSz = j;

   //cout << "NEW " << endl;
   //for (i=0; i < TransSz; i++)
   //   cout << TransAry[i] << " ";
   //cout << endl;
}

void Dbase_Ctrl_Blk::print_trans(){
  cout << Cid << " " << Tid << " " << TransSz;
  for (int i=0; i < TransSz; i++)
    cout << " " << TransAry[i];
  cout << endl;
}


void Dbase_Ctrl_Blk::alloc_idlists()
{
   //allocate space for Idlists
   Idlists.resize(NumF1);
   for (int i=0; i < NumF1; i++){
      Idlists[i] = new idlist;   
   }
}

void Dbase_Ctrl_Blk::make_vertical(){
   int i, j; //track the position in trans, counting BranchIt
   int pi, pj; //track the position in trans, not counting BranchIt
   int scope;
   
  //convert current transaction into vertical format
  for (i=0, pi=0; i < TransSz; i++){
    if (TransAry[i] == BranchIt) continue;

    scope=0;
    for (j=i+1, pj=pi; scope >= 0 && j < TransSz; j++){
      if (TransAry[j] == BranchIt) scope--;
      else{
         scope++;
         pj++;
      }
    }
    
    idnode nn(Cid, pi,pj);
    //cout << "push " << TransAry[i] << " " <<  pi << " " << pj << endl;
    Idlists[TransAry[i]]->push_back(nn);
    pi++;
  }
}

void Dbase_Ctrl_Blk::print_vertical(){
  int i;
  for (i=0; i < NumF1; i++){
    cout << "item " << Dbase_Ctrl_Blk::FreqIdx[i] << endl;
    cout << *Idlists[i];
  }
}
