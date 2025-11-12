from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

class ResultsTable(QWidget):
    """table widge for displaying query results"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = None
        self._init_ui()

    def _init_ui(self):
        """init the ui"""
        layout = QVBoxLayout(self)

        #header with title and export
        header_layout = QHBoxLayout()

        title = QLabel("Query Results")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.export_btn = QPushButton("Export Results...")
        self.export_btn.clicked.connect(self._export_results)
        self.export_btn.setEnabled(False)
        header_layout.addWidget(self.export_btn)

        layout.addLayout(header_layout)

        #results table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        #info label
        self.info_label = QLabel("No results")
        self.info_label.setStyleSheet("font-size: 11px; color: #888; padding: 5px;")
        layout.addWidget(self.info_label)

    def display_results(self, result):
        """
        display query results in the table

        args:
            result: duckdb query result object
        """
        try:
            #fetch all rows
            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]

            #store for export
            self.current_results = (rows, columns)

            #update the table
            self.table.clear()
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

            #populate table
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEdittable)
                    self.table.setItem(row_idx, col_idx, item)

            #resize colums to content
            self.table.resizeColumnsToContents()

            #update info
            self.info_label.setText(f"{len(rows)} row(s), {len(columns)} colum(s)")
            self.export_btn.setEnabled(True)
        
        except Exception as e:
            self.info_label.setText(f"Error displaying results: {str(e)}")
            self.export_btn.setEnabled(False)

    def _export_results(self):
        """export current results to file"""
        if not self.current_results:
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "CSV Files (*.csv);;Parquet Files (*.parquet);;All Files (*)"
        )

        if file_path:
            try:
                rows, columns = self.current_results

                #simple csv export
                # TODO: use duckdb export for better performance
                import csv
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)

                QMessageBox.information(self, "Export Successful", f"Results exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting results:\n\n{str(e)}")
    
    def clear(self):
        """clear the results table"""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.current_results = None
        self.info_label.setText("No results")
        self.export_btn.setEnabled(False)