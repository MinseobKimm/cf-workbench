#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct AbsoluteValueComparator {
    bool operator()(ll a, ll b) const {
        if (llabs(a) != llabs(b)) return llabs(a) > llabs(b);
        return a > b;
    }
};

using AbsoluteValuePriorityQueue = priority_queue<ll, vector<ll>, AbsoluteValueComparator>;


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
