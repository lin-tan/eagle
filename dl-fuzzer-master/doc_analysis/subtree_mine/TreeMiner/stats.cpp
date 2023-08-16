#include "stats.h"

//static initializations
double Stats::tottime = 0;
double Stats::sumtime = 0;
int Stats::sumcand = 0;
int Stats::sumlarge = 0;

//function defs

//Stats::Stats(): vector<iterstat *>(){}

void Stats::add(iterstat &is){
   push_back(is);
   sumtime += is.time;
   sumcand += is.numcand;
   sumlarge += is.numlarge;
}

void Stats::add(int cand, int freq, double time, double avgtid){
  iterstat *is = new iterstat(cand, freq, time, avgtid);
  push_back(*is);
  sumtime += is->time;
  sumcand += is->numcand;
  sumlarge += is->numlarge;
}

void Stats::incrcand(int pos, int ncand)
{
   if (pos >= size()) resize(pos+1);
   (*this)[pos].numcand += ncand;
   sumcand += ncand;
}

void Stats::incrlarge(int pos, int nlarge)
{
   if (pos >= size()) resize(pos+1);
   (*this)[pos].numlarge += nlarge;
   sumlarge += nlarge;
}

void Stats::incrtime(int pos, double ntime)
{
   if (pos >= size()) resize(pos+1);
   (*this)[pos].time += ntime;
   sumtime += ntime;
}


ostream& operator << (ostream& fout, Stats& stats){
  //fout << "SIZE " << stats.size() << endl;
  for (int i=0; i<stats.size(); i++){
    fout << "[ " << i+1 << " " << stats[i].numcand << " "
	 << stats[i].numlarge << " " << stats[i].time << " "
	 << stats[i].avgtid << " ] ";
  }
  fout << "[ SUM " << stats.sumcand << " " << stats.sumlarge << " "
       << stats.sumtime << " ] ";
  fout << stats.tottime;
  return fout;
}
