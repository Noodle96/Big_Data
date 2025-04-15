#include <bits/stdc++.h>
#define all(x) x.begin(),x.end()
#define msg(str,str2) cout << str << str2<< endl
using namespace std;

using ll = long long;
using ld = long double;
using uint = unsigned int;
using ull = unsigned long long;
template<typename T>
using pair2 = pair<T, T>;
using pii = pair<int, int>;
using pli = pair<ll, int>;
using pll = pair<ll, ll>;

#define pb push_back
#define mp make_pair

int gcd(int a,int b){
	if(a%b==0) return b;
	else return gcd(b,a%b);
}

clock_t startTime;
double getCurrentTime() {
	return (double)(clock() - startTime) / CLOCKS_PER_SEC;
}

vector<string> dataFile;
unordered_map<string, int> hashDataFile;

void solve(){
	ifstream archivo("data/english_parte_0.txt");
	string linea;
	int cont = 0;
	if (archivo.is_open()) {
		while (std::getline(archivo, linea)) {
			// istringstream ss(linea);
			// cout << "[" << nombreArchivo << "] " << linea << endl;

			// cont ++;
			// dataFile.pb(linea);
			hashDataFile[linea]++;
		}
		archivo.close();
	} else {
		std::cerr << "Error al abrir el archivo"  <<std::endl;
	}

	// cout << "cont: " << cont << endl;
	// cout << "size datafile: " << dataFile.size() << endl;
	cout << "size hashDataFile: " << hashDataFile.size() << endl;
}

int main(){
	ios_base::sync_with_stdio(false);
	cin.tie(0);
	#ifdef DEBUG
		freopen("input.txt","r",stdin);
		freopen("output.txt","w",stdout);
	#endif
	startTime = clock();
	solve();
	cout << "Execution Time: " << getCurrentTime() << endl;
	return 0;
}
// data 194433
	// with cont++: 0.0050 seg
	// with pb in vector 0.0170 seg
	// with hash 0.0850 seg

// data 101901844
	// with cont++: 2.5 seg
	// with pb in vector 7.2 seg
	// with hash 17 seg