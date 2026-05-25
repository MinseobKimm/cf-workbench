#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct TreeIndependentSet {
    int n;
    vector<vector<int>> tree;
    vector<ll> weight;
    vector<array<ll, 2>> dp;
    vector<int> chosen;

    TreeIndependentSet(vector<vector<int>> tree, vector<ll> weight)
        : n((int)tree.size()), tree(move(tree)), weight(move(weight)), dp(n) {
    }

    void dfs(int u, int parent) {
        dp[u][0] = 0;
        dp[u][1] = weight[u];

        for (int v : tree[u]) {
            if (v == parent) continue;
            dfs(v, u);
            dp[u][0] += max(dp[v][0], dp[v][1]);
            dp[u][1] += dp[v][0];
        }
    }

    void restore(int u, int parent, int take) {
        if (take) chosen.push_back(u);

        for (int v : tree[u]) {
            if (v == parent) continue;
            if (take) restore(v, u, 0);
            else restore(v, u, dp[v][1] > dp[v][0]);
        }
    }

    pair<ll, vector<int>> solve(int root = 0) {
        chosen.clear();
        dfs(root, -1);
        int take_root = dp[root][1] > dp[root][0];
        restore(root, -1, take_root);
        return {max(dp[root][0], dp[root][1]), chosen};
    }
};


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
