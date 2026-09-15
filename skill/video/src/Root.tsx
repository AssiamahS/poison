import React from "react";
import { Composition } from "remotion";
import { Explainer, ExplainerProps, FPS } from "./Explainer";

const defaultProps: ExplainerProps = {
  width: 1536,
  height: 1024,
  title: "poison",
  frames: [{ image: "frame-1.svg", caption: "Frame one", durationSec: 3 }],
  transitionSec: 0.6,
  tailSec: 1.5,
};

export const Root: React.FC = () => (
  <Composition
    id="Explainer"
    component={Explainer}
    fps={FPS}
    width={defaultProps.width}
    height={defaultProps.height}
    durationInFrames={90}
    defaultProps={defaultProps}
    calculateMetadata={({ props }) => {
      const body = props.frames.reduce((s, f) => s + f.durationSec, 0);
      const total = 1 + body + props.tailSec; // 1s title card
      return {
        durationInFrames: Math.max(30, Math.round(total * FPS)),
        width: props.width,
        height: props.height,
      };
    }}
  />
);
