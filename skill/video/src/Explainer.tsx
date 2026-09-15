import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const FPS = 30;

export type Frame = {
  image: string;        // file in public/, svg or png
  caption?: string;     // one line under the picture
  audio?: string;       // optional narration wav in public/
  durationSec: number;  // how long this frame stays
};

export type ExplainerProps = {
  width: number;
  height: number;
  title: string;
  frames: Frame[];
  transitionSec: number;
  tailSec: number;
};

const TitleCard: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 14 } });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#FBF7EE", justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontFamily: "'Marker Felt', 'Chalkboard SE', 'Avenir Next', sans-serif",
          fontSize: 88,
          color: "#2B2B2B",
          transform: `scale(${0.85 + 0.15 * s})`,
          opacity,
          textAlign: "center",
          padding: "0 80px",
        }}
      >
        {title}
      </div>
    </AbsoluteFill>
  );
};

const Slide: React.FC<{ f: Frame; durationFrames: number; transitionFrames: number }> = ({
  f,
  durationFrames,
  transitionFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = interpolate(frame, [0, transitionFrames], [0, 1], { extrapolateRight: "clamp" });
  const zoom = spring({ frame, fps, config: { damping: 200, stiffness: 40 } });
  const captionIn = spring({ frame: frame - 6, fps, config: { damping: 16 } });
  return (
    <AbsoluteFill style={{ background: "#FBF7EE" }}>
      <AbsoluteFill style={{ opacity: fadeIn, transform: `scale(${1.02 - 0.02 * zoom})` }}>
        <Img src={staticFile(f.image)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </AbsoluteFill>
      {f.caption ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 36,
            display: "flex",
            justifyContent: "center",
            transform: `translateY(${(1 - captionIn) * 40}px)`,
            opacity: captionIn,
          }}
        >
          <div
            style={{
              background: "rgba(43,43,43,0.88)",
              color: "#fff",
              fontFamily: "'Avenir Next', 'Helvetica Neue', sans-serif",
              fontSize: 30,
              padding: "14px 28px",
              borderRadius: 14,
              maxWidth: "80%",
            }}
          >
            {f.caption}
          </div>
        </div>
      ) : null}
      {f.audio ? <Audio src={staticFile(f.audio)} /> : null}
    </AbsoluteFill>
  );
};

export const Explainer: React.FC<ExplainerProps> = ({ title, frames, transitionSec, tailSec }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const titleFrames = fps;
  const transitionFrames = Math.round(transitionSec * fps);
  let cursor = titleFrames;
  const slides = frames.map((f, i) => {
    const d = Math.round(f.durationSec * fps) + (i === frames.length - 1 ? Math.round(tailSec * fps) : 0);
    const from = cursor;
    cursor += Math.round(f.durationSec * fps);
    return (
      <Sequence key={i} from={from} durationInFrames={d} premountFor={fps}>
        <Slide f={f} durationFrames={d} transitionFrames={transitionFrames} />
      </Sequence>
    );
  });
  return (
    <AbsoluteFill style={{ background: "#FBF7EE" }}>
      <Sequence from={0} durationInFrames={titleFrames + transitionFrames}>
        <TitleCard title={title} />
      </Sequence>
      {slides}
      <Sequence from={Math.max(0, durationInFrames - Math.round(0.5 * fps))}>
        <AbsoluteFill style={{ background: "#FBF7EE", opacity: 0 }} />
      </Sequence>
    </AbsoluteFill>
  );
};
