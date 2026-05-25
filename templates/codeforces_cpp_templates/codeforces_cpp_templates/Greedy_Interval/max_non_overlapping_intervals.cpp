#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct Interval {
    ll start;
    ll end;
};

int max_non_overlapping_intervals(vector<Interval> intervals) {
    sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
        if (a.end != b.end) return a.end < b.end;
        return a.start < b.start;
    });

    int count = 0;
    ll last_end = -LINF;

    for (const Interval& interval : intervals) {
        if (interval.start < last_end) continue;
        ++count;
        last_end = interval.end;
    }

    return count;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
