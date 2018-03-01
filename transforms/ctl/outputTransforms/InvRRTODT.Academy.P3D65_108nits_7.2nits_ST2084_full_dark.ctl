import "ACESlib.Utilities";
import "ACESlib.OutputTransforms";



const OutputParameters OT_PARAMS = 
{
    0.0001, 7.2, 108.0,   // black luminance, mid-point luminance, peak white luminance
    {{ 0.68000, 0.32000},{ 0.26500, 0.69000},{ 0.15000, 0.06000},{ 0.3127, 0.329}},  // encoding primaries
    {{ 0.68000, 0.32000},{ 0.26500, 0.69000},{ 0.15000, 0.06000},{ 0.3127, 0.329}},  // limiting primaries
    0,      // 0: ST-2084 (PQ), 1: BT.1886 (Rec.709/2020 settings), 2: sRGB (mon_curve w/ presets), 3: gamma 2.6, 4: linear (no EOTF), 5: HLG
    0,      // 0: dark, 1: dim, 2, 2: normal
    true,   // stretch black luminance to a PQ code value of 0
    false,  // D60_sim
    false   // smpte_range
};


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
    float cv[3] = {rIn, gIn, bIn};

    float aces[3] = invOutputTransform( cv, OT_PARAMS);

    rOut = aces[0];
    gOut = aces[1];
    bOut = aces[2];
    aOut = aIn;
}