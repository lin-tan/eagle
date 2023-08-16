#include <algorithm>

#include "hashtable.h"
#include "eqclass.h"
#include "treeminer.h"


///////////////////
//FreqHT
///////////////////

void FreqHT::add(int iter, Eqclass *eq){
   vector<int> *iset;
   int phval = 0;
   int i;
   for (i=0; i < eq->prefix().size(); i++)
      if (eq->prefix()[i] != BranchIt) phval += eq->prefix()[i];
   
   
   int hval = 0;
   int scope, scnt;
   list<Eqnode *>::iterator ni = eq->nlist().begin();
   for (; ni != eq->nlist().end(); ni++){
      iset = new vector<int>(eq->prefix());
      scnt = eq->get_scope((*ni)->pos, scope); //what is the scope of node.pos
      while(scnt > scope){
         iset->push_back(BranchIt);
         scnt--;
      }
      iset->push_back((*ni)->val);
      hval = phval + (*ni)->val;
      if (chtable[iter] == NULL) chtable[iter] = new cHTable(FHTSIZE);
      int hres = chtable[iter]->hash_funct()(hval);
      chtable[iter]->insert(cHTPair(hres, iset));
      //cout << "ADD " << hres << " xx " << *iset << endl;
   }
}

bool eqcmp(vector<int> *v1, vector<int> *v2)
{
   if (v1->size() != v2->size()) return false;
   for (int i=0; i < v1->size(); i++){
      if ((*v1)[i] != (*v2)[i]) return false;
   }
   return true;
}

bool FreqHT::find(int iter, vector<int> &cand, int hval)
{
   if (chtable[iter] == NULL) return false;

   int hres = chtable[iter]->hash_funct()(hval);   
   cHTFind p = chtable[iter]->equal_range(hres);
   
   //cout << "FIND " << hres << " xx  " << cand << endl;
   cHTable::iterator hi = p.first;
   for (; hi!=p.second; hi++){
      if (eqcmp(&cand, (*hi).second)) return true;
   }
   return false;
}
