import "ACESlib.Utilities";
import "ACESlib.OutputTransforms";



const float Y_MIN = 0.02;                       // black luminance (cd/m^2)
const float Y_MID = 4.8;                        // mid-point luminance (cd/m^2)
const float Y_MAX = 48.0;                       // peak white luminance (cd/m^2)

const float SLOPE_MIN = 0.0;                    // min-point slope
const float SLOPE_MID = 1.55;                   // mid-point slope
const float SLOPE_MAX = 0.0;                    // max-point slope
    
/*  
These determine the position of the middle coefficient in either the low or 
high part of the tonescale. This affects the "bendiness" of the curve.
This is ordinarily calculated automatically but is exposed here for flexibility.
*/
const float PCT_LOW = 0.35;                     // the % between Y_MIN and Y_MID
const float PCT_HIGH = 0.90;                    // the % between Y_MID and Y_MAX

const Chromaticities DISPLAY_PRI = P3D65_PRI;   // encoding primaries (device setup)
const Chromaticities LIMITING_PRI = P3D65_PRI;  // limiting primaries

const int EOTF = 0;                             // 0: ST-2084 (PQ)
                                                // 1: BT.1886 (Rec.709/2020 settings) 
                                                // 2: sRGB (mon_curve w/ presets)
                                                // 3: gamma 2.6
                                                // 4: linear (no EOTF)
                                                // 5: HLG

const int SURROUND = 0;                         // 0: dark ( NOTE: this is the only active setting! )
                                                // 1: dim ( *inactive* - selecting this will have no effect )
                                                // 2: normal ( *inactive* - selecting this will have no effect )

const bool STRETCH_BLACK = false;               // stretch black luminance to a PQ code value of 0
const bool D60_SIM = false;                       
const bool LEGAL_RANGE = false;


void main
(
	input varying float rIn,
	input varying float gIn,
	input varying float bIn,
	input varying float aIn,
	output varying float rOut,
	output varying float gOut,
	output varying float bOut,
	output varying float aOut
)
{
    float aces[3] = {rIn, gIn, bIn};

    float cv[3] = outputTransform_wPct( aces, Y_MIN,
                                             Y_MID,
                                             Y_MAX,
                                             SLOPE_MIN,
                                             SLOPE_MID,
                                             SLOPE_MAX,
                                             PCT_LOW,
                                             PCT_HIGH,
                                             DISPLAY_PRI,
                                             LIMITING_PRI,
                                             EOTF,
                                             SURROUND,
                                             STRETCH_BLACK,
                                             D60_SIM,
                                             LEGAL_RANGE );

    rOut = cv[0];
    gOut = cv[1];
    bOut = cv[2];
    aOut = aIn;
}