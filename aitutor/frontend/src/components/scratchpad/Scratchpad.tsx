import React, { useState, useRef } from "react";
import { ReactSketchCanvas, ReactSketchCanvasRef } from "react-sketch-canvas";
import "./scratchpad.scss";

const styles = {
  border: "0.0625rem solid #9c9c9c",
  borderRadius: "0.25rem",
};

const Scratchpad = () => {
  const [strokeColor, setStrokeColor] = useState("black");
  const [strokeWidth, setStrokeWidth] = useState(4);
  const [isErasing, setErasing] = useState(false);
  const canvasRef = useRef<ReactSketchCanvasRef>(null);

  const toggleEraser = () => {
    setErasing(!isErasing);
    if (canvasRef.current) {
      if (!isErasing) {
        canvasRef.current.eraseMode(true);
      } else {
        canvasRef.current.eraseMode(false);
      }
    }
  };

  return (
    <>
      <div className="scratchpad-controls">
        <input
          type="color"
          value={strokeColor}
          onChange={(e) => setStrokeColor(e.target.value)}
        />
        <input
          type="range"
          min="1"
          max="20"
          value={strokeWidth}
          onChange={(e) => setStrokeWidth(parseInt(e.target.value, 10))}
        />
        <button onClick={toggleEraser} className="icon-button">
          <span className="material-symbols-outlined">
            {isErasing ? "edit" : "ink_eraser"}
          </span>
        </button>
        <button onClick={() => canvasRef.current?.clearCanvas()} className="icon-button">
          <span className="material-symbols-outlined">
            delete
          </span>
        </button>
      </div>
      <ReactSketchCanvas
        ref={canvasRef}
        style={styles}
        width="100%"
        height="100%"
        strokeWidth={strokeWidth}
        strokeColor={strokeColor}
        canvasColor="rgba(255, 255, 255, 0.5)"
      />
    </>
  );
};

export default Scratchpad;
