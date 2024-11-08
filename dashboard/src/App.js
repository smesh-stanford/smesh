import React from "react";
import './styles.css';

import CsvViewer from "./CsvViewer";

class App extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div>
        <CsvViewer />
      </div>
    );
  }
}
export default App;