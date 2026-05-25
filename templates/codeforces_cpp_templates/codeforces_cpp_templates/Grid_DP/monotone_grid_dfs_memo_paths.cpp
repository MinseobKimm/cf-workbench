#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct MonotoneGridPaths {
    int height;
    int width;
    vector<vector<int>> grid;
    vector<vector<ll>> memo;
    int dx[4] = {1, -1, 0, 0};
    int dy[4] = {0, 0, 1, -1};

    MonotoneGridPaths(vector<vector<int>> grid)
        : height((int)grid.size()), width(grid.empty() ? 0 : (int)grid[0].size()), grid(move(grid)), memo(height, vector<ll>(width, -1)) {
    }

    ll dfs(int x, int y) {
        if (x == height - 1 && y == width - 1) return 1;

        ll& result = memo[x][y];
        if (result != -1) return result;
        result = 0;

        for (int direction = 0; direction < 4; ++direction) {
            int nx = x + dx[direction];
            int ny = y + dy[direction];

            if (nx < 0 || nx >= height || ny < 0 || ny >= width) continue;
            if (grid[nx][ny] >= grid[x][y]) continue;
            result += dfs(nx, ny);
        }

        return result;
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
