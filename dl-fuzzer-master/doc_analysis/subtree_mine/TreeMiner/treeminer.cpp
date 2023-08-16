#include<iostream>
#include <unistd.h>
#include <algorithm>
#include <stdio.h>
//#include <stl.h>
#include <list>

//headers
#include "treeminer.h"
#include "timetrack.h"
#include "calcdb.h"
#include "eqclass.h"
#include "stats.h"
#include "hashtable.h"

using namespace std;

//global vars
char infile[300];
Dbase_Ctrl_Blk *DCB;
Stats stats;

double MINSUP_PER;
int MINSUPPORT=-1;
int DBASE_MAXITEM;
int DBASE_NUM_TRANS;
int MAX_ITER = -1;

//default flags
bool output = false; //don't print freq subtrees
bool output_idlist = false; //don't print idlist
bool count_unique = true; //count support only once per tree
bool use_fullpath = false; //use reduced scope to conserve mem

sort_vals sort_type = incr; //default is to sort in increasing order
alg_vals alg_type = treeminer; //default is to find all freq patterns

prune_vals prune_type = noprune; //prune
FreqHT FK; //to store freq subtrees for pruning

vector<int> *ITCNT = NULL; //used for sorting F1
bool F1cmp(int x, int y){
   bool res = false;
   if ((*ITCNT)[x] < (*ITCNT)[y]) res = true;

   if (sort_type == incr) return res;
   else return !res;
}
   

void parse_args(int argc, char **argv)
{
   extern char * optarg;
   int c;

   if (argc < 2)
     cout << "usage: treeminer -i<infile> -s <support>\n";
   else{
     while ((c=getopt(argc,argv,"a:bfi:lop:s:S:m:uz:"))!=-1){
       switch(c){
         case 'a':
            alg_type = (alg_vals) atoi(optarg);
            break;
         case 'b':
            Dbase_Ctrl_Blk::binary_input= true;
            break;
         case 'f':
            use_fullpath = true;
            break;
         case 'i': //input files
            sprintf(infile,"%s",optarg);
            break;
         case 'l': //print idlists along with freq subtrees
            output=true;
            output_idlist = true;
            break;
         case 'o': //print freq subtrees
            output = true;
            break;
         case 'p':
            prune_type = (prune_vals) atoi(optarg);
            break;
        case 's': //support value for L2
            MINSUP_PER = atof(optarg);
            break;
         case 'S': //absolute support
            MINSUPPORT = atoi(optarg);
            break;
         case 'm':  // max iteration
            MAX_ITER = atoi(optarg);
            break;
         case 'u': //count support multiple times per tree
            count_unique = false;
            break;
         case 'z':
            sort_type = (sort_vals) atoi(optarg);
            break;
       }               
     }
   }
}

void get_F1()
{
  TimeTracker tt;
  double te;

  int i, j, it;
  const int arysz = 10;
  
  vector<int> itcnt(arysz,0); //count item frequency
  vector<int> flgs(arysz,-1);

  tt.Start();

  DBASE_MAXITEM=0;
  DBASE_NUM_TRANS = 0;
  
   while(DCB->get_next_trans())
   {
      //cout << "TRANS " << DCB->Cid << " " << DCB->Tid
      //     << " " << DCB->TransSz << " -- ";
      //for (i=0; i < DCB->TransSz; i++)
      //   cout << " " << DCB->TransAry[i];
      //cout << endl;
      
      for (i=0; i < DCB->TransSz; i++){
         it = DCB->TransAry[i];
         if (it == BranchIt) continue;
         
         if (it >= DBASE_MAXITEM){
            itcnt.resize(it+1,0);
            flgs.resize(it+1,-1);
            DBASE_MAXITEM = it+1;
            //cout << "IT " << DBASE_MAXITEM << endl;
         }
         
         if (count_unique){
            if(flgs[it] == DCB->Cid) continue;
            else flgs[it] = DCB->Cid;
         }
         itcnt[it]++;
      }
      
      if (DCB->MaxTransSz < DCB->TransSz) DCB->MaxTransSz = DCB->TransSz;     
      DBASE_NUM_TRANS++;
   }
   
   //for (i=0; i < DCB->TransSz; i++){
   //   it = DCB->TransAry[i];
   //   if (it != BranchIt){
   //      cout << it << " " << itcnt[it] << endl;
   //   }
   //}

   //set the value of MINSUPPORT
   if (MINSUPPORT == -1)
     MINSUPPORT = (int) (MINSUP_PER*DBASE_NUM_TRANS+0.5);
   
   if (MINSUPPORT<1) MINSUPPORT=1;
   cout<<"DBASE_NUM_TRANS : "<< DBASE_NUM_TRANS << endl;
   cout<<"DBASE_MAXITEM : "<< DBASE_MAXITEM << endl;
   cout<<"MINSUPPORT : "<< MINSUPPORT << " (" << MINSUP_PER << ")" << endl;

   //count number of frequent items
   DCB->NumF1 = 0;
   for (i=0; i < DBASE_MAXITEM; i++)
     if (itcnt[i] >= MINSUPPORT)
       DCB->NumF1++;

   int *it_order = new int[DBASE_MAXITEM];
   for (i=0; i < DBASE_MAXITEM; i++)
      it_order[i] = i;
   
   if (sort_type != nosort){
      ITCNT = &itcnt;
      sort(&it_order[0], &it_order[DBASE_MAXITEM], F1cmp);
   }

   //construct forward and reverse mapping from items to freq items
   DCB->FreqIdx = new int [DCB->NumF1];
   DCB->FreqMap = new int [DBASE_MAXITEM];
   for (i=0,j=0; i < DBASE_MAXITEM; i++) {
      if (itcnt[it_order[i]] >= MINSUPPORT) {
         //if (output) cout << i << " " << it_order[i] 
         //                 << " - " << itcnt[it_order[i]] << endl;
         // if (output) cout << i << " - " << itcnt[it_order[i]] << endl;
         DCB->FreqIdx[j] = it_order[i];
         DCB->FreqMap[it_order[i]] = j;
         j++;
      }
      else DCB->FreqMap[it_order[i]] = -1;
   }
   
   //cout<< "F1 - " << DCB->NumF1 << " " << DBASE_MAXITEM << endl;  
   
   if (sort_type != nosort){
      ITCNT = NULL;
      delete [] it_order;
   }
   
   te = tt.Stop();
   stats.add(DBASE_MAXITEM, DCB->NumF1, te);

}

list<Eqclass *> * get_F2()
{
  int i,j;
  int it1, it2;
  int scnt;
  
  TimeTracker tt;
  double te;

  tt.Start();

  list<Eqclass *> *F2list = new list<Eqclass *>;

  //itcnt2 is a matrix of pairs p, p.first is count, p.second is flag
  int **itcnt2 = new int*[DCB->NumF1];
  int **flgs = new int*[DCB->NumF1];
  //unsigned int **itcnt2 = new unsigned int *[DCB->NumF1];
  for (i=0; i < DCB->NumF1; i++){
    itcnt2[i] = new int [DCB->NumF1];
    flgs[i] = new int [DCB->NumF1];
    //cout << "alloc " << i << " " << itcnt2[i] << endl;
    for (j=0; j < DCB->NumF1; j++){
      itcnt2[i][j] = 0;
      flgs[i][j] = -1;
    }
  }
    
   DCB->alloc_idlists();
   
   while(DCB->get_next_trans())
   {
      DCB->get_valid_trans();
      DCB->make_vertical();
      //DCB->print_trans();
      //count a pair only once per cid
      for (i=0; i < DCB->TransSz; i++){
         it1 = DCB->TransAry[i];
         if (it1 != BranchIt){
            scnt = 0;
            for (j=i+1; scnt >= 0 && j < DCB->TransSz; j++){
               it2 = DCB->TransAry[j];
               if (it2 != BranchIt){
		 scnt++;
		 if (count_unique){
		   if (flgs[it1][it2] == DCB->Cid) continue;
		   else flgs[it1][it2] = DCB->Cid;
		 }
		 //cout << "cnt " << it1 << " " << it2 << endl;
		 itcnt2[it1][it2]++;
               }
               else scnt--;
            }
         }
      }
   }                           
   
   int F2cnt=0;

   // count frequent patterns and generate eqclass
   Eqclass *eq;
   for (i=0; i < DCB->NumF1; i++) {
      eq = NULL;
      for (j=0; j < DCB->NumF1; j++) {
	//cout << "access " << i << " " << j << endl;
         if (itcnt2[i][j] >= MINSUPPORT){
            F2cnt++;
            if (eq == NULL){
               eq = new Eqclass;
               eq->prefix().push_back(i);
            }
	    eq->add_node(j,0);
            
	    //if (output) 
	    //  cout << DCB->FreqIdx[i] << " " << DCB->FreqIdx[j] 
            //	   << " - " << itcnt2[i][j] << endl;
         }
      }   
      if (eq != NULL) F2list->push_back(eq);
   }
   
   for (i=0; i < DCB->NumF1; i++) {
     //cout << "dealloc " << i << " " << itcnt2[i] << endl;
     delete [] itcnt2[i];
     //cout << "dealloc " << i << " " << flgs[i] << endl;
     delete [] flgs[i];
   }

   delete [] itcnt2;
   delete [] flgs;
   
   
   //cout << "F2 - " << F2cnt << " " << DCB->NumF1 * DCB->NumF1 << endl;
   te = tt.Stop();
   stats.add(DCB->NumF1 * DCB->NumF1, F2cnt, te);

   return F2list;
}

static bool notfrequent (Eqnode &n){
  //cout << "IN FREQ " << n.sup << endl;
  if (n.sup >= MINSUPPORT) return false;
  else return true;
}


void check_ins(idlist *l1, idlist *l2, Eqnode *ins, 
                int st1, int st2, int en1, int en2){
   static idnode *n1, *n2;
   static ival_type cmpval;

   bool found_flg = false;
   int pos1 = st1; //temporary position holder for n1 ival
   bool next2; //should we go to next n2 ival?

   //for each ival in n2, find the closest parent in n1
   int tpos = ins->tlist.size();
   while(st2 < en2){
      n1 = &(*l1)[pos1];
      n2 = &(*l2)[st2];

      next2 = true; //by default we go to next n2 ival
      cmpval = ival::compare(n1->itscope, n2->itscope);
      switch (cmpval){
      case sup: 
         //n2 was under some n1

         if (n1->path_equal(*n2)){
            if (en1-st1 > 1 || use_fullpath){
               //  ins->tlist.push_back(idnode(n2->cid, n1->parscope, 
               //                            n1->itscope.lb, n2->itscope));

               ins->add_list(n2->cid, n1->parscope, 
                             n1->itscope.lb, n2->itscope);
            }
            else{
               //ins->tlist.push_back(idnode(n2->cid,n2->itscope));
               ins->add_list(n2->cid,n2->itscope);
            }
            if (!count_unique) ins->sup++;
            found_flg = true;
         }
         
         next2 = false;
         break;
      case before: 
         //check next n1 ival for same n2 ival
         next2 = false; 
         break;
      }

      if (next2 || pos1+1 == en1){ //go to next n2 ival
         pos1 = st1;
         st2++;
      }
      else pos1++; //go to next n1 ival
   }
   
   if (found_flg && count_unique) ins->sup++;
}

   
void check_outs(idlist *l1, idlist *l2, Eqnode *outs,
                int st1, int st2, int en1, int en2){
   static idnode *n1, *n2;
   static ival_type cmpval;

   bool found_flg = false;
   bool next2;
   int pos1 = st1;
   
   //for each n2 ival find if there is a sibling to the left
   int tpos = outs->tlist.size();
   while(st2 < en2){
      n1 = &(*l1)[pos1];
      n2 = &(*l2)[st2];

      next2 = true;
      cmpval = ival::compare(n1->itscope, n2->itscope);
      switch (cmpval){
      case sup:
         next2 = false;
         break;
      case before: 
         //n1 is before n2. Check if n1.par is subset of or equal to n2.par
         if (n1->path_equal(*n2)){
            if (en1 - st1 > 1 || use_fullpath){
               //outs->tlist.push_back(idnode(n2->cid, n1->parscope, 
               //                            n1->itscope.lb, n2->itscope));
               outs->add_list(n2->cid, n1->parscope, 
                              n1->itscope.lb, n2->itscope);
            }
            else{
               //outs->tlist.push_back(idnode(n2->cid,n2->itscope));
               outs->add_list(n2->cid,n2->itscope);
            }
            if (!count_unique) outs->sup++;
            found_flg = true;
         }
         next2 = false;
         break;
      }
      if (next2 || pos1+1 == en1){ //go to next n2 ival
         pos1 = st1;
         st2++;
      }
      else pos1++; //go to next n1 ival
   }
   if (found_flg && count_unique) outs->sup++;
}


void get_intersect(idlist *l1, idlist *l2, Eqnode *ins, Eqnode *outs)
{
   static idnode *n1, *n2;

   int i1 = 0, i2 = 0;
   int e1, e2;

   //cout << "GISECT:\n";
   //cout << *l1;
   //cout << *l2;
   
   while (i1 < l1->size() && i2 < l2->size()){
      n1 = &(*l1)[i1];
      n2 = &(*l2)[i2];

      //look for matching cids
      if (n1->cid < n2->cid) i1++;
      else if (n1->cid > n2->cid) i2++;
      else{
         //cids match
         e1 = i1;
         e2 = i2;

         //check the cid end positions in it1 and it2
         while (e1 < l1->size() && (*l1)[e1].cid == n1->cid) e1++;
         while (e2 < l2->size() && (*l2)[e2].cid == n2->cid) e2++;

         //cout << "ISECT " << i1 << " " << i2 << " " << e1 << " " << e2 << endl;
         //increment support if candidate found
         if (ins) check_ins(l1, l2, ins, i1, i2, e1, e2);
         if (outs) check_outs(l1, l2, outs, i1, i2, e1, e2);

         //restore index to end of cids
         i1 = e1;
         i2 = e2;
      }
   }
}


bool lexsmaller(vector<int> &subtree, vector<int> &cand)
{
   int i,j;

   for (i=0, j=0; i < subtree.size() && j < cand.size();){

      if (subtree[i] > cand[j]){
         if (cand[j] != BranchIt) return false;
         else{
            while (cand[j] == BranchIt) j++;
            if (subtree[i] > cand[j]) return false;
            else if (subtree[i] < cand[j]) return true;
            else return false;
         }
         
      }
      else if (subtree[i] < cand[j]){
         if (subtree[i] != BranchIt) return true;
         else{
            while(subtree[i] == BranchIt) i++;
            if (subtree[i] > cand[j]) return false;
            else if (subtree[i] < cand[j]) return true;
            else return true;
         }
      }
      else{
         i++;
         j++;
      }
   }
   return false;
}


Eqnode *test_node(int iter, Eqclass *eq, int val, int pos)
{
   Eqnode *eqn = NULL;
   
   //if noprune, return with a new Eqnode
   if (prune_type == noprune){
      eqn = new Eqnode(val,pos);
      return eqn;
   }
   
   //perform pruning

   //prune based on frequent subtree
   static vector<int> cand;
   static vector<int> subtree;
 
   int hval;
   int scope, scnt;

   //form the candidate preifx
   cand = eq->prefix();
   scnt = eq->get_scope(pos, scope); //what is the scope of node.pos

   while(scnt > scope){
      cand.push_back(BranchIt);
      scnt--;
   }
   cand.push_back(val);

   //check subtrees
   int omita, omitb;
   bool res = true;
   //omit i-th item (omita) and associated BranchIt (omitb)
   int i,j,k;

   for (i=iter-3; i >= 0; i--){
      //find pos for i-th item
      for (j=0,k=0; j < cand.size(); j++){
         if (cand[j] != BranchIt){
            if (k == i){
               omita = j;
               break;
            }
            else k++;
         }
      }
      
      //find pos for associated BranchIt
      scnt = 0;
      for(j++; j < cand.size() && scnt >= 0; j++){
         if (cand[j] == BranchIt) scnt--;
         else scnt++;
      }
      if (scnt >= 0) omitb = cand.size();
      else omitb = j-1;

      //cout << "OMIT " << i << " " << omita << " " << omitb << endl;

      hval = 0;
      subtree.clear();
      bool rootless = false;
      scnt = 0;
      for (k=0; k < cand.size() && !rootless; k++){
         if (k != omita && k != omitb){
            subtree.push_back(cand[k]);
            if (cand[k] != BranchIt){
               hval += cand[k];
               scnt++;
            }
            else scnt--;
            if (scnt <= 0) rootless = true;
            
         }
      }

      //cout << "LEXTEST " << subtree << " vs " << cand;
   
      //skip a rootless subtree
      if (!rootless && lexsmaller(subtree, cand)){
         //cout << " -- SMALLER ";
         res = FK.find(iter-1, subtree, hval);  
         //cout << ((res)? " ** FOUND\n":" ** NOTFOUND\n");
         if (!res) return NULL; //subtree not found!
      }
      //else cout << " -- GREATER " << endl;
   }
   
  
   if (res) eqn = new Eqnode(val,pos);
   else eqn = NULL;

   return eqn;
}


void enumerate_freq(Eqclass *eq, int iter)
{
   TimeTracker tt;
   Eqclass *neq;
   list<Eqnode *>::iterator ni, nj;
   Eqnode *ins, *outs;

   if (prune_type == noprune) eq->sort_nodes(); //doesn't work with pruning

   //cout << "FX " << *eq << endl;

   for (ni = eq->nlist().begin(); ni != eq->nlist().end(); ++ni){
      neq = new Eqclass;
      neq->set_prefix(eq->prefix(),*(*ni));
      tt.Start();
      for (nj = eq->nlist().begin(); nj != eq->nlist().end(); ++nj){ 
         if ((*ni)->pos < (*nj)->pos) continue;

         ins = outs = NULL;
         if ((*ni)->pos > (*nj)->pos){
            outs = test_node(iter, neq, (*nj)->val, (*nj)->pos);
         }
         else{ 
            outs = test_node(iter, neq, (*nj)->val, (*nj)->pos);
            ins = test_node(iter, neq, (*nj)->val, neq->prefix().size()-1);
         }  

         //cout << "prefix " << neq->print_prefix() << " -- " 
         //     << *(*nj) << " " << outs_depth << endl;
         if (ins || outs)
            get_intersect(&(*ni)->tlist, &(*nj)->tlist, ins, outs);

         if (outs){
            stats.incrcand(iter-1);
            //cout << "OUTS " << *outs;
            if (notfrequent(*outs)) delete outs;
            else{
               neq->add_node(outs);
               stats.incrlarge(iter-1);
            }
         }
         if (ins){
            // cout << "INS " << *ins;
            stats.incrcand(iter-1);
            if (notfrequent(*ins)) delete ins;
            else{
               neq->add_node(ins);
               stats.incrlarge(iter-1);
            }
         }
      }
      stats.incrtime(iter-1, tt.Stop());
      if (!neq->nlist().empty()){
         if (output){
            cout << "ITER " << iter-1 << endl;
            cout << *neq;
         }
         if (prune_type == prune) FK.add(iter,neq);
         if (MAX_ITER<0 || iter<=MAX_ITER) enumerate_freq(neq, iter+1);
      }
      delete neq;
   }
}

void form_f2_lists(Eqclass *eq)
{
   list<Eqnode *>::iterator ni;
   idlist *l1, *l2;
   Eqnode *ins=NULL, *outs=NULL;
   int pit, nit;
   TimeTracker tt;
   
   tt.Start();
   pit = eq->prefix()[0];
   l1 = DCB->Idlists[pit];
   for (ni=eq->nlist().begin(); ni != eq->nlist().end(); ++ni){
      nit = (*ni)->val;
      l2 = DCB->Idlists[nit];
      ins = (*ni);
      //cout << "LISTS " << pit << " " << nit << " " << l1->size() 
      //     << " " << l2->size() << " " << ins->tlist.size() << endl;
      get_intersect(l1, l2, ins, outs);
      //cout << "f2prefix " << eq->prefix() << endl;
      //cout << "f2 " << *ins;
   }
   stats.incrtime(1,tt.Stop());
}

void get_Fk(list<Eqclass *> &F2list){
   Eqclass *eq;

   while(!F2list.empty()){
      eq = F2list.front();
      form_f2_lists(eq);
      if (output) cout << *eq;
      if (prune_type == prune) FK.add(2, eq);
      switch(alg_type){
      case treeminer:
         enumerate_freq(eq, 3); 
         break;
      case maxtreeminer:
         cout << "NOT IMPLEMENTED\n";
         break;
      }
      delete eq;
      F2list.pop_front();
   }
}

int main(int argc, char **argv)
{
   TimeTracker tt;
   tt.Start(); 
   parse_args(argc, argv); 
  
   DCB = new Dbase_Ctrl_Blk(infile); 
   get_F1();
   list<Eqclass *> *F2list = get_F2();

   //DCB->print_vertical();
   get_Fk(*F2list);

   // for (int i=0; i < stats.size(); i++){
   //    cout << "F" << i+1 << " - ";
   //    cout << stats[i].numlarge << " " << stats[i].numcand << endl;
   // }
   
   double tottime = tt.Stop();
   stats.tottime = tottime;

   // cout << stats << endl;
   
   cout << "TIME = " << tottime << endl;

   //write results to summary file
   ofstream summary("summary.out", ios::app); 
   summary << "VTREEMINER ";
   switch(sort_type){
   case incr: summary << "INCR "; break;
   case decr: summary << "DECR "; break;
   default: break;
   }
   switch(prune_type){
   case prune: summary << "PRUNE "; break;
   deafult: break;
   }
   if (!count_unique) summary << "MULTIPLE ";
   if (use_fullpath) summary << "FULLPATH ";

   summary << infile << " " << MINSUP_PER << " "
           << DBASE_NUM_TRANS << " " << MINSUPPORT << " ";
   summary << stats << endl;
   summary.close();
   
   exit(0);
}



