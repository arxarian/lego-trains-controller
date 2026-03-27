import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    spacing: 5

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

        CheckBox {
            text: "Rails Ids"
            checked: Globals.railIdVisible
            onClicked: Globals.railIdVisible = checked
        }
    }

    RowLayout {
        TextField {
            id: textFieldRails

            text: "2,1B,4,6"

            Layout.fillWidth: true
        }

        Button {
            text: "Plan"
            onClicked: planner.plan(textFieldRails.displayText)
        }
    }

    RowLayout {
        TextField {
            id: textFieldReserveRails

            text: "3A16:6A8"

            Layout.fillWidth: true
        }

        Button {
            text: "Reserve"
            onClicked: planner.reserve(textFieldReserveRails.displayText)
        }

        Button {
            text: "Unreserve"
            onClicked: planner.unreserve(textFieldReserveRails.displayText)
        }
    }
}
