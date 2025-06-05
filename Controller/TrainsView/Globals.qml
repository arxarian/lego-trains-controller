pragma Singleton

import QtQuick

QtObject {
    readonly property QtObject rail: QtObject {
        readonly property int straight: 0
        readonly property int curved: 1
        readonly property int switchRail: 2
    }

    readonly property QtObject dir: QtObject {
        readonly property int up: 1
        readonly property int down: -1
    }

    readonly property real curveRadius: 1358
    readonly property real basicAngleIncrement: 22.5
    readonly property real defaultRotation: 90
}
