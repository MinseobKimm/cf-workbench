#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

ll sum_after_zero_undo(const vector<ll>& values) {
    vector<ll> st;

    for (ll value : values) {
        if (value == 0) {
            if (!st.empty()) st.pop_back();
        } else {
            st.push_back(value);
        }
    }

    return accumulate(st.begin(), st.end(), 0LL);
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
