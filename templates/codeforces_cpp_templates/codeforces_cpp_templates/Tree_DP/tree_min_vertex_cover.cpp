#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct TreeVertexCover {
    int n;
    vector<vector<int>> tree;
    vector<array<int, 2>> dp;

    TreeVertexCover(vector<vector<int>> tree) : n((int)tree.size()), tree(move(tree)), dp(n) {
    }

    void dfs(int u, int parent) {
        dp[u][0] = 0;
        dp[u][1] = 1;

        for (int v : tree[u]) {
            if (v == parent) continue;
            dfs(v, u);
            dp[u][0] += dp[v][1];
            dp[u][1] += min(dp[v][0], dp[v][1]);
        }
    }

    int solve(int root = 0) {
        dfs(root, -1);
        return min(dp[root][0], dp[root][1]);
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
