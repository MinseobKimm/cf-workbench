#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll tsp_cycle_bitmask(const vector<vector<ll>>& cost, int start = 0, ll no_edge = -1) {
    int n = (int)cost.size();
    int full = (1 << n) - 1;
    vector<vector<ll>> dp(1 << n, vector<ll>(n, LINF));

    dp[1 << start][start] = 0;

    for (int mask = 0; mask <= full; ++mask) {
        for (int u = 0; u < n; ++u) {
            if (dp[mask][u] == LINF) continue;

            for (int v = 0; v < n; ++v) {
                if (mask & (1 << v)) continue;
                if (cost[u][v] == no_edge) continue;

                int next_mask = mask | (1 << v);
                dp[next_mask][v] = min(dp[next_mask][v], dp[mask][u] + cost[u][v]);
            }
        }
    }

    ll answer = LINF;
    for (int u = 0; u < n; ++u) {
        if (u == start) continue;
        if (cost[u][start] == no_edge) continue;
        answer = min(answer, dp[full][u] + cost[u][start]);
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
