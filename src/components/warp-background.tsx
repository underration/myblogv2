import {GrainGradient, type GrainGradientProps} from '@paper-design/shaders-react';

export default function WarpBackground(props: GrainGradientProps) {

    const defaultProps = {
        speed: 0.4,
        rotation: 0.5,
        style: { width: '100%', height: '100%' }
    };

    return <GrainGradient {...defaultProps} {...props} style={{ ...defaultProps.style, ...props.style }} />;

}