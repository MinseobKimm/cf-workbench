#include <bits/stdc++.h>
using namespace std;

using ll = long long;

const int INF = 1000000000;
const ll LINF = (1LL << 62);

struct Interval {
    ll start;
    ll end;
};

int min_rooms_priority_queue(vector<Interval> intervals) {
    sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
        if (a.start != b.start) return a.start < b.start;
        return a.end < b.end;
    });

    priority_queue<ll, vector<ll>, greater<ll>> current_end_times;
    int answer = 0;

    for (const Interval& interval : intervals) {
        while (!current_end_times.empty() && current_end_times.top() <= interval.start) {
            current_end_times.pop();
        }

        current_end_times.push(interval.end);
        answer = max(answer, (int)current_end_times.size());
    }

    return answer;
}


void solve() {
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();
    return 0;
}
