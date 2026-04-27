#include <bits/stdc++.h>
#define all(x) x.begin(), x.end()
using namespace std;
using ll = long long;
using i64 = int64_t;
using i32 = int32_t;
using ld = long double;
using uint = unsigned int;
using ull = unsigned long long;
template <typename T>
using pair2 = pair<T, T>;
using pii = pair<int, int>;
using pli = pair<ll, int>;
using pll = pair<ll, ll>;
using vll = vector<ll>;

#define pb push_back
#define mp make_pair

clock_t startTime;
double getCurrentTime(){
    return (double)(clock() - startTime) / CLOCKS_PER_SEC;
}

void solve(){
    // Leer el archivo llamada palabras.txt
    ifstream file("4GB.txt");
    if (!file.is_open()){
        cerr << "Error al abrir el archivo palabras.txt\n";
        return;
    }
    unordered_map<string, int> wordcount;
    string word;
    while (file >> word){
        // debemos de considerar el caso cuando en una linea se traiga mas de una palabra
        istringstream iss(word);
        string subword;
        while (iss >> subword){
            word = subword;
            wordcount[word]++;
        }
    }

    // escribir el resultado en un archivo llamado resultado.txt
    ofstream output("resultado.txt");
    if (!output.is_open()){
        cerr << "Error al abrir el archivo resultado.txt\n";
        return;
    }
    for (const auto &pair : wordcount){
        output << pair.first << " " << pair.second << "\n";
    }
}

void solve2(){
    ifstream file("test.txt");
    if (!file.is_open()){
        cerr << "Error al abrir el archivo test.txt\n";
        return;
    }
    // leer string
    string line;
    while (getline(file, line)){
    }
    cout << line.size() << "\n";
    startTime = clock();
    // ll ans = 0;
    // for(int i = 0; i < line.size(); i++){
    //     ans++;
    // }
    line.find_last_of(" \n");
    cout << "Tiempo: " << getCurrentTime() << " segundos\n";
}

int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

#ifdef DEBUG
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif

    int t;
    // cin >> t;
    t = 1;
    while (t--){
        solve2();
    }
    return 0;
}