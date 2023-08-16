#ifndef __eqclass_h
#define __eqclass_h

#include <iostream>
#include <list>
#include <vector>

#include "treeminer.h"
#include "calcdb.h"
#include "idlist.h"

class Eqnode{
public:
   int val; //item value
   int pos; //which node is it connected to in parent prefix
   int sup; //support
   idlist tlist; //scope list for this item
   
   Eqnode(int v, int p, int s=0): val(v), pos(p), sup(s){}
   bool find_in_tlist(vector<int> &par, int lit, ival &it, int stpos=0);

   static bool supcmp (Eqnode *n1, Eqnode *n2){
      bool res = false;
      if ((n1)->sup < (n2)->sup) res = true;
      
      if (sort_type == incr) return res;
      else return !res;
   }
   void add_list(int c, ival &it)
   {
//       if (tlist.size() > 0){
//          idnode *idn = &tlist.back();
//          if (idn->cid == c && idn->itscope == it) return;
//       }
      
      tlist.push_back(idnode(c,it));
   }
   
   void add_list(int c, vector<int> &pscope, int lit, ival &ivl)
   {
//       if (tlist.size() > 0){
//          idnode *idn = &tlist.back();
//          vector<int> ps = pscope;
//          ps.push_back(lit);
//          if (idn->cid == c && 
//              idn->itscope == ivl && 
//              idn->parscope == ps) return;
//       }
      
      tlist.push_back(idnode(c, pscope, lit, ivl));
   }
   
   friend ostream & operator<<(ostream& ostr, Eqnode& eqn);
};


class Eqclass{
private:
   vector<int> _prefix; //class prefix
   list<Eqnode *> _nodelist; //class nodes
   
public:
   ~Eqclass();
   vector<int> &prefix(){ return _prefix; }
   list<Eqnode *> &nlist(){ return _nodelist; }
   void add_node(int val, int pos, int sup=0);
   void add_node(Eqnode *eqn);
   int item(int n);
   int get_scope(int pos, int &scope);
   void set_prefix(vector<int> &pref, Eqnode &node);
   void sort_nodes(){
      if (sort_type == nosort) return;
      _nodelist.sort(Eqnode::supcmp);
   }
   void print();
   ostream & print_prefix(ostream &fout=cout);
   friend ostream & operator<<(ostream& ostr, Eqclass& eq);
};

#endif
 
