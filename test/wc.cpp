#include <bits/stdc++.h>
#define all(x) x.begin(),x.end()
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
using vll = vector<ll>;

#define pb push_back
#define mp make_pair

const ll INF = 1e18;

ll gcd(ll a,ll b){
    if(a%b==0) return b;
    else return gcd(b,a%b);
}

clock_t startTime;
double getCurrentTime() {
    return (double)(clock() - startTime) / CLOCKS_PER_SEC;
}

void solve(){
    std::string filename = "../txt/500MB_test_borrar.txt";  // Cambia esto por tu archivo
    std::ifstream infile(filename);
    if (!infile) {
        std::cerr << "No se pudo abrir el archivo: " << filename << std::endl;
        return;
    }
    startTime = clock();
    std::unordered_map<std::string, int> wordCount;
    std::string line, word;
    while (std::getline(infile, line)) {
        // std::stringstream ss(line);
        // while (ss >> word) {
        //     wordCount[word]++;
        // }
        wordCount[line]++;
    }
    infile.close();
    cout << "Tiempo de ejecución: " << getCurrentTime() << " segundos" << endl;

    startTime = clock();
    // Imprimir frecuencias
    for (const auto& pair : wordCount) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    cout << "Tiempo de ejecución: " << getCurrentTime() << " segundos" << endl;
}
int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    #ifdef DEBUG
        freopen("input.txt","r",stdin);
        freopen("output.txt","w",stdout);
    #endif
    solve();
    return 0;
}