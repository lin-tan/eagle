#ifndef __hasht_h
#define __hasht_h

#include <map> 
#include <ext/hash_map>
#include <list>
#include <vector>
#include <functional>

#define HASHNS __gnu_cxx
using namespace std;

#include "eqclass.h"

#define FHTSIZE 100 
//for pruning candidate subtrees
typedef HASHNS::hash_multimap<int, vector<int> *, HASHNS::hash<int>, equal_to<int> > cHTable;
typedef pair < cHTable::iterator, cHTable::iterator> cHTFind;
typedef cHTable::value_type cHTPair;

class FreqHT{
   vector<cHTable *> chtable;
public:
   FreqHT(int sz = FHTSIZE): chtable(sz, ((cHTable *) NULL)){}
   ~FreqHT(){ clearall(); }

   void clearall(){
      for (int i=0; i < chtable.size(); i++){
         if (chtable[i]){
            cHTable::iterator hi = chtable[i]->begin();
            for (; hi != chtable[i]->end(); hi++){
               delete (*hi).second;
            }
            chtable[i]->clear();
         }
      }
   }
   
   void add(int iter, Eqclass *eq);
   bool find(int iter, vector<int> &cand, int hval);
};

#endif
