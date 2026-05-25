#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll matrix_chain_min_cost(const vector<ll>& dimension) {
    int n = (int)dimension.size() - 1;
    if (n <= 0) return 0;

    vector<vector<ll>> dp(n, vector<ll>(n, 0));

    for (int length = 2; length <= n; ++length) {
        for (int left = 0; left + length - 1 < n; ++left) {
            int right = left + length - 1;
            dp[left][right] = LINF;

            for (int mid = left; mid < right; ++mid) {
                ll cost = dp[left][mid] + dp[mid + 1][right] + dimension[left] * dimension[mid + 1] * dimension[right + 1];
                dp[left][right] = min(dp[left][right], cost);
            }
        }
    }

    return dp[0][n - 1];
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
