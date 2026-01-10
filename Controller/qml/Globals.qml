pragma Singleton

import QtQuick
import TrainView

QtObject {
    readonly property QtObject dir: QtObject {
        readonly property string forward: "forward"
        readonly property string reverse: "reverse"
    }

    property bool gridVisible: false
    property bool trackFrameVisible: false
    property bool rotationPointsVisible: false
    property bool railIdVisible: true

    property int selectedRail: Rail.Straight   // TODO - fix RailType registration
    property int selectedMarker: -1
}
