#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

int min_coin_count_unbounded(const vector<int>& coins, int target) {
    vector<int> dp(target + 1, INF);
    dp[0] = 0;

    for (int coin : coins) {
        for (int sum = coin; sum <= target; ++sum) {
            if (dp[sum - coin] == INF) continue;
            dp[sum] = min(dp[sum], dp[sum - coin] + 1);
        }
    }

    return dp[target] == INF ? -1 : dp[target];
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
