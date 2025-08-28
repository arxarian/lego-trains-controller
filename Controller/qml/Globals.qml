pragma Singleton

import QtQuick
import TrainView

QtObject {
    readonly property QtObject dir: QtObject {
        readonly property string start: "start"
        readonly property string end: "end"
    }

    property bool gridVisible: false
    property bool trackFrameVisible: false
    property bool rotationPointsVisible: false

    property Item selectedTrack: null
    property int selectedType: Rail.Straight   // TODO - fix RailType registration
}
