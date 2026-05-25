#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

vector<vector<char>> transitive_closure(vector<vector<char>> reachable) {
    int n = (int)reachable.size();

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            if (!reachable[i][k]) continue;
            for (int j = 0; j < n; ++j) {
                reachable[i][j] = reachable[i][j] || reachable[k][j];
            }
        }
    }

    return reachable;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
