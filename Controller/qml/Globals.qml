pragma Singleton

import QtQuick

QtObject {
    readonly property QtObject dir: QtObject {
        readonly property int up: 1
        readonly property int down: -1
    }

    property bool gridVisible: false
    property bool trackFrameVisible: false
    property bool rotationPointsVisible: false

    property Item selectedTrack: null
}
