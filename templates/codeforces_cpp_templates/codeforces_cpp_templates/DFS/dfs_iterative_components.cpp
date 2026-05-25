#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

vector<vector<int>> dfs_components_iterative(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> visited(n, 0);
    vector<vector<int>> components;

    for (int start = 0; start < n; ++start) {
        if (visited[start]) continue;

        vector<int> component;
        stack<int> st;
        st.push(start);
        visited[start] = 1;

        while (!st.empty()) {
            int u = st.top();
            st.pop();
            component.push_back(u);

            for (int v : graph[u]) {
                if (visited[v]) continue;
                visited[v] = 1;
                st.push(v);
            }
        }

        components.push_back(component);
    }

    return components;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
