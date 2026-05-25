#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll count_coin_combinations_unbounded(const vector<int>& coins, int target) {
    vector<ll> dp(target + 1, 0);
    dp[0] = 1;

    for (int coin : coins) {
        for (int sum = coin; sum <= target; ++sum) {
            dp[sum] += dp[sum - coin];
        }
    }

    return dp[target];
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
