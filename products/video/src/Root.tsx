import "./index.css";
import { Composition } from "remotion";
import { WordOfTheDay } from "./WordOfTheDay";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="WordOfTheDay" component={WordOfTheDay} durationInFrames={450} fps={30} width={1920} height={1080} />
    </>
  );
};
