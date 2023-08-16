#ifndef __idlist_H
#define __idlist_H
 
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

//basic idnode, tidnode, idlist declarations
enum ival_type {equals, sup, sub, before, after, overlap};

//interval class
class ival{
public:
   int lb; //lower bound of scope range
   int ub; //upper bound of scope range
   
   ival(int l=0, int u=0): lb(l), ub(u){};

   bool operator == (ival &iv)
   {
      return (iv.lb == lb && iv.ub == ub);
   }
   
   static ival_type compare(ival &n1, ival &n2){
      ival_type retval;
      if (n1.lb == n2.lb && n1.ub == n2.ub) retval = equals; //n1 equals n2
      else if (n1.lb < n2.lb && n1.ub >= n2.ub) retval = sup; //n1 contains n2
      else if (n1.lb > n2.lb && n1.ub <= n2.ub) retval = sub; //n2 contains n1
      else if (n1.ub < n2.lb) retval = before; //n1 comes before n2
      else if (n2.ub < n1.lb) retval = after; //n1 comes after n2
      else{ 
         retval = overlap;
         //cout << "wrong case in compare_interval: ";
         //cout << "[" << n1.lb << "," << n1.ub << "]";
         //cout << " [" << n2.lb << "," << n2.ub << "]" << endl;
      }
      return retval;
   };

   friend ostream & operator<<(ostream& ostr, ival& idn);
};

class idnode{
public:
   int cid; //Tree Id
   ival itscope; //node's scope
   vector<int> parscope; //node's parent scope
   
   idnode(int c=0, int l=0, int u=0): cid(c), itscope(l,u){};

   idnode(int c, ival &it){
      cid = c;
      itscope = it;
   }

   idnode(int c, vector<int> &pscope, int lit, ival &ivl){
      cid = c;
      itscope = ivl;
      parscope = pscope;
      parscope.push_back(lit);      
   }

   bool path_equal(idnode &idn){
      int i;
      for (i=0; i < parscope.size(); i++){
         if (parscope[i] != idn.parscope[i]) return false;
      }
      return true;
   }
   friend ostream & operator<<(ostream& ostr, idnode& idn);
};

class idlist: public vector<idnode>{
   friend ostream & operator<<(ostream& fout, idlist& idl);
};

extern ostream & operator<<(ostream& fout, vector<int> &vec);
#endif
