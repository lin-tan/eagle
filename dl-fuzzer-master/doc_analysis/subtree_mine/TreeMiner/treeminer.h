#ifndef __treeminer_H
#define __treeminer_H

#include <vector>
#include <functional>

#define BranchIt -1 //-1 indicates a branch in the tree

//enums
enum sort_vals {nosort, incr, decr};
enum alg_vals {treeminer, maxtreeminer};
enum prune_vals {noprune, prune};
  
//externs
extern double MINSUP_PER;
extern int MINSUPPORT;
extern int DBASE_MAXITEM;
extern int DBASE_NUM_TRANS;

extern bool output;
extern bool output_idlist;

extern sort_vals sort_type;  
extern alg_vals alg_type;
extern prune_vals prune_type;

using namespace std;

template<class T>
struct delnode: public unary_function<T, void>{
   void operator() (T x){ delete x; }
};


#endif
