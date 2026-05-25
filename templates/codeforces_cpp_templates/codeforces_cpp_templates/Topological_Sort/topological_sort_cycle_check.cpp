#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

pair<bool, vector<int>> topological_sort(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> indegree(n, 0);

    for (int u = 0; u < n; ++u) {
        for (int v : graph[u]) ++indegree[v];
    }

    queue<int> q;
    for (int i = 0; i < n; ++i) {
        if (indegree[i] == 0) q.push(i);
    }

    vector<int> order;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        order.push_back(u);

        for (int v : graph[u]) {
            --indegree[v];
            if (indegree[v] == 0) q.push(v);
        }
    }

    return {(int)order.size() == n, order};
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
