#include "idlist.h"

ostream & operator<<(ostream& ostr, ival& idn){
   ostr << "[" << idn.lb << ", " << idn.ub << "]";
   return ostr;
}

ostream & operator<<(ostream& ostr, idnode& idn){
   ostr << idn.cid << " " << idn.itscope << " -- " << idn.parscope;
   return ostr;
}         

ostream & operator<<(ostream& fout, idlist& idl)
{
   for (int j=0; j < idl.size(); j++){
      fout << "\t" << idl[j] << endl;
   }
   return fout;
}

ostream & operator<<(ostream& fout, vector<int> &vec){
  for (int i=0; i < vec.size(); i++)
     fout << vec[i] << " ";
  return fout;
}
