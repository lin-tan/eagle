#ifndef __DATABASE_H
#define __DATABASE_H

#include <iostream>
#include <fstream>
#include <vector>
#include "treeminer.h"
#include "idlist.h"

#define ITSZ sizeof(int)
#define DCBBUFSZ 2048
#define TRANSOFF 3

class Dbase_Ctrl_Blk{
private:

  //vars related to the horizontal format
   ifstream fd;
   int buf_size;
   int * buf;
   int cur_blk_size; 
   int cur_buf_pos;
   int endpos;
   char readall;   
   static int *PvtTransAry;
   
   //vars for the vertical format

public:
   static int NumF1;   //number of freq items
   static int *FreqMap; //mapping of freq items, i.e., item to freq_idx
   static int *FreqIdx; //freq_idx to original item value

   //vars related to the horizontal format
   static int *TransAry;
   static int TransSz;
   static int Tid;
   static int Cid;
   static int MaxTransSz;
   static bool binary_input;

   //vars related to vertical format
   vector<idlist *> Idlists;

   //function definitions
   Dbase_Ctrl_Blk(const char *infile, const int buf_sz=DCBBUFSZ);
   ~Dbase_Ctrl_Blk();
   
   //functions for horizontal format
   void get_next_trans_ext();
   void get_first_blk();
   int get_next_trans();
   void get_valid_trans();
   void print_trans();
   int eof(){return (readall == 1);}

   //functions for vertical format
   void make_vertical();
   void print_vertical();
   void alloc_idlists();
};

#endif //__DATABASE_H





