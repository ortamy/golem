import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import words from "./data/words.json";

type Letter = {glyph: string; name: string; picture: string; meaning: string};
type Word = {id: string; hebrew: string; paleo: string; translit: string; gloss: string; letters: Letter[]; synthesis: string; keywords: string[]; confidence: number};

const word = words[0] as Word;
const parchment = "#ede0c8";
const paper = "#faf3e0";
const ink = "#2c1810";
const muted = "#765f4b";
const gold = "#b8860b";

const fade = (frame: number, from: number, to: number) => interpolate(frame, [from, to], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});

export const WordOfTheDay: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = frame / fps;
  const sceneOne = fade(frame, 0, 12) * (1 - fade(frame, 116, 126));
  const sceneTwo = fade(frame, 116, 132) * (1 - fade(frame, 260, 276));
  const sceneThree = fade(frame, 260, 276);

  return (
    <AbsoluteFill style={{backgroundColor: parchment, color: ink, fontFamily: "'EB Garamond', Georgia, serif", overflow: "hidden"}}>
      <div style={{position: "absolute", inset: 48, border: `1px solid ${gold}`, opacity: 0.45}} />
      <div style={{position: "absolute", top: 76, left: 100, color: gold, fontSize: 22, letterSpacing: "0.18em", textTransform: "uppercase"}}>слово дня</div>
      <div style={{position: "absolute", top: 76, right: 100, color: muted, fontSize: 18}}>GOLEM / {String(Math.floor(seconds)).padStart(2, "0")}:00</div>

      <AbsoluteFill style={{opacity: sceneOne, alignItems: "center", justifyContent: "center"}}>
        <div style={{color: muted, fontSize: 28, marginBottom: 34}}>палео-сборка</div>
        <div style={{display: "flex", gap: 38, direction: "ltr"}}>
          {Array.from(word.paleo).map((glyph, index) => {
            const progress = spring({frame: frame - index * 14, fps, config: {damping: 14, stiffness: 110}});
            return <div key={`${glyph}-${index}`} style={{color: gold, fontFamily: "'Noto Sans Phoenician', 'Segoe UI Historic', serif", fontSize: 190, lineHeight: 1, opacity: progress, transform: `translateY(${interpolate(progress, [0, 1], [45, 0])}px) scale(${interpolate(progress, [0, 1], [0.72, 1])})`}}>{glyph}</div>;
          })}
        </div>
        <div style={{fontSize: 42, marginTop: 48, letterSpacing: "0.12em"}}>{word.translit}</div>
      </AbsoluteFill>

      <AbsoluteFill style={{opacity: sceneTwo, padding: "170px 150px 100px"}}>
        <div style={{fontSize: 38, color: muted, marginBottom: 30}}>Буквы слова</div>
        <div style={{display: "grid", gridTemplateColumns: `repeat(${word.letters.length}, 1fr)`, gap: 14, height: 570}}>
          {word.letters.map((letter, index) => {
            const progress = spring({frame: frame - 124 - index * 8, fps, config: {damping: 16, stiffness: 100}});
            return <div key={letter.name} style={{backgroundColor: paper, border: `1px solid ${gold}`, padding: "25px 18px", opacity: progress, transform: `translateY(${interpolate(progress, [0, 1], [38, 0])}px)`}}>
              <div style={{color: gold, fontFamily: "'Noto Sans Phoenician', 'Segoe UI Historic', serif", fontSize: 86, textAlign: "center"}}>{letter.glyph}</div>
              <div style={{fontSize: 29, fontWeight: 700, marginTop: 18}}>{letter.name}</div>
              <div style={{fontSize: 24, color: muted, marginTop: 42}}>образ</div>
              <div style={{fontSize: 30, marginTop: 5}}>{letter.picture}</div>
              <div style={{fontSize: 24, color: muted, marginTop: 42}}>смысл</div>
              <div style={{fontSize: 28, lineHeight: 1.15, marginTop: 5}}>{letter.meaning}</div>
            </div>;
          })}
        </div>
      </AbsoluteFill>

      <AbsoluteFill style={{opacity: sceneThree, alignItems: "center", justifyContent: "center", textAlign: "center"}}>
        <div style={{fontSize: 34, color: muted, marginBottom: 24}}>сборка</div>
        <div style={{fontSize: 66, maxWidth: 1400, lineHeight: 1.1}}>{word.synthesis}</div>
        <div style={{fontSize: 34, color: gold, marginTop: 42}}>{word.hebrew} · {word.translit} · {word.gloss}</div>
        <div style={{marginTop: 90, padding: "14px 44px", backgroundColor: ink, color: parchment, fontSize: 30, letterSpacing: "0.28em"}}>GOLEM</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};