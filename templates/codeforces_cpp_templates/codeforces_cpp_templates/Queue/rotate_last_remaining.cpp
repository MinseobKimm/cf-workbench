#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

int last_remaining_after_rotate(int n) {
    queue<int> q;

    for (int i = 1; i <= n; ++i) q.push(i);

    while (q.size() > 1) {
        q.pop();
        q.push(q.front());
        q.pop();
    }

    return q.front();
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
