#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

int min_cost_to_reach_target(const vector<ll>& value, const vector<int>& cost, ll target) {
    int max_cost = accumulate(cost.begin(), cost.end(), 0);
    vector<ll> dp(max_cost + 1, -LINF);
    dp[0] = 0;

    int n = (int)value.size();
    for (int i = 0; i < n; ++i) {
        for (int c = max_cost; c >= cost[i]; --c) {
            if (dp[c - cost[i]] == -LINF) continue;
            dp[c] = max(dp[c], dp[c - cost[i]] + value[i]);
        }
    }

    for (int c = 0; c <= max_cost; ++c) {
        if (dp[c] >= target) return c;
    }

    return -1;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
