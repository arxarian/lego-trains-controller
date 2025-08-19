import QtQuick
import QtQuick.Controls

Column {
    id: root
    property int trackType: Rail.Straight

    Row {
        CheckBox {
            text: "Grid"
            checked: Globals.gridVisible
            onClicked: Globals.gridVisible = checked
        }

        CheckBox {
            text: "Track Frame"
            checked: Globals.trackFrameVisible
            onClicked: Globals.trackFrameVisible = checked
        }

        CheckBox {
            text: "Rotation Points"
            checked: Globals.rotationPointsVisible
            onClicked: Globals.rotationPointsVisible = checked
        }
    }

    Row {
        Button {
            checked: root.trackType === Rail.Straight
            checkable: true
            text: "Straight"
            onClicked: root.trackType = Rail.Straight
        }

        Button {
            checked: root.trackType === Rail.Curved
            checkable: true
            text: "Curved"
            onClicked: root.trackType = Rail.Curved
        }

        Button {
            checked: root.trackType === Rail.Switch
            checkable: true
            text: "Switch"
            onClicked: root.trackType = Rail.Switch
        }
    }
}
