#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll knapsack_01_max_value(const vector<int>& weight, const vector<ll>& value, int capacity) {
    vector<ll> dp(capacity + 1, 0);
    int n = (int)weight.size();

    for (int i = 0; i < n; ++i) {
        for (int w = capacity; w >= weight[i]; --w) {
            dp[w] = max(dp[w], dp[w - weight[i]] + value[i]);
        }
    }

    return dp[capacity];
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
