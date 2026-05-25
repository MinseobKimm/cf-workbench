#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll shortest_directed_cycle(vector<vector<ll>> dist) {
    int n = (int)dist.size();

    for (int i = 0; i < n; ++i) dist[i][i] = 0;

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            if (dist[i][k] == LINF) continue;
            for (int j = 0; j < n; ++j) {
                if (dist[k][j] == LINF) continue;
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }

    ll answer = LINF;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == j) continue;
            if (dist[i][j] == LINF || dist[j][i] == LINF) continue;
            answer = min(answer, dist[i][j] + dist[j][i]);
        }
    }

    return answer == LINF ? -1 : answer;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
