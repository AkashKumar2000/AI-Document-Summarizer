import React from "react";

export default function Slider({
  min = 2000,
  max = 20000,
  step = 1000,
  value,
  onChange,
}) {
  return (
    <input
      className="slider"
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
    />
  );
}
