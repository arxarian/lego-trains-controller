pragma Singleton

import QtQuick

QtObject {
    readonly property QtObject dir: QtObject {
        readonly property string start: "start"
        readonly property string end: "end"
    }

    property bool gridVisible: false
    property bool trackFrameVisible: false
    property bool rotationPointsVisible: false

    property Item selectedTrack: null
}
