#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct FloydWarshall {
    int n;
    vector<vector<ll>> dist;
    vector<vector<int>> next_vertex;

    FloydWarshall(int n) : n(n), dist(n, vector<ll>(n, LINF)), next_vertex(n, vector<int>(n, -1)) {
        for (int i = 0; i < n; ++i) {
            dist[i][i] = 0;
            next_vertex[i][i] = i;
        }
    }

    void add_edge(int from, int to, ll weight) {
        if (weight >= dist[from][to]) return;
        dist[from][to] = weight;
        next_vertex[from][to] = to;
    }

    void run() {
        for (int k = 0; k < n; ++k) {
            for (int i = 0; i < n; ++i) {
                if (dist[i][k] == LINF) continue;
                for (int j = 0; j < n; ++j) {
                    if (dist[k][j] == LINF) continue;
                    if (dist[i][j] <= dist[i][k] + dist[k][j]) continue;
                    dist[i][j] = dist[i][k] + dist[k][j];
                    next_vertex[i][j] = next_vertex[i][k];
                }
            }
        }
    }

    vector<int> restore_path(int from, int to) const {
        if (next_vertex[from][to] == -1) return {};

        vector<int> path;
        int current = from;
        path.push_back(current);

        while (current != to) {
            current = next_vertex[current][to];
            if (current == -1) return {};
            path.push_back(current);
        }

        return path;
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
