#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll interval_merge_knuth(const vector<ll>& a) {
    int n = (int)a.size();
    if (n == 0) return 0;

    vector<ll> prefix(n + 1, 0);
    for (int i = 0; i < n; ++i) prefix[i + 1] = prefix[i] + a[i];

    vector<vector<ll>> dp(n, vector<ll>(n, 0));
    vector<vector<int>> opt(n, vector<int>(n, 0));

    for (int i = 0; i < n; ++i) opt[i][i] = i;

    for (int length = 2; length <= n; ++length) {
        for (int left = 0; left + length - 1 < n; ++left) {
            int right = left + length - 1;
            ll sum = prefix[right + 1] - prefix[left];
            dp[left][right] = LINF;

            int from = opt[left][right - 1];
            int to = opt[left + 1][right];
            from = max(from, left);
            to = min(to, right - 1);

            for (int mid = from; mid <= to; ++mid) {
                ll candidate = dp[left][mid] + dp[mid + 1][right] + sum;
                if (candidate < dp[left][right]) {
                    dp[left][right] = candidate;
                    opt[left][right] = mid;
                }
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
