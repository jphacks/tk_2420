import { generateYOLOAnnotations, generateBoundingBoxesFromYOLO } from './yoloUtils';
import { BoundingBox, YOLOAnnotation, LabelInfo } from './types';


describe('generateYOLOAnnotations', () => {
  test('should correctly convert bounding boxes to YOLO annotations', () => {
    const boundingBoxes: BoundingBox[] = [
      { x: 0, y: 0, width: 640, height: 480, label_id: 0, color: 'red' },
    ];
    const imageWidth = 640;
    const imageHeight = 480;

    const expected: YOLOAnnotation[] = [
      {
        class_id: 0,
        x_center: 0.5,
        y_center: 0.5,
        width: 1,
        height: 1,
      },
    ];
    expect(generateYOLOAnnotations(boundingBoxes, imageWidth, imageHeight)).toEqual(expected);
  });

  test('should correctly convert bounding boxes to YOLO annotations', () => {
    const boundingBoxes: BoundingBox[] = [
      { x: 320, y: 240, width: 160, height: 120, label_id: 1, color: 'green' },
    ];
    const imageWidth = 640;
    const imageHeight = 480;

    const expected: YOLOAnnotation[] = [
      {
        class_id: 1,
        x_center: 0.625,
        y_center: 0.625,
        width: 0.25,
        height: 0.25,
      },
    ];
    expect(generateYOLOAnnotations(boundingBoxes, imageWidth, imageHeight)).toEqual(expected);
  });

  test('should correctly convert multiple bounding boxes', () => {
    const boundingBoxes: BoundingBox[] = [
      { x: 0, y: 0, width: 640, height: 480, label_id: 0, color: 'red' },
      { x: 320, y: 240, width: 160, height: 120, label_id: 1, color: 'green' },
    ];
    const imageWidth = 640;
    const imageHeight = 480;

    const expected: YOLOAnnotation[] = [
      {
        class_id: 0,
        x_center: 0.5,
        y_center: 0.5,
        width: 1,
        height: 1,
      },
      {
        class_id: 1,
        x_center: 0.625,
        y_center: 0.625,
        width: 0.25,
        height: 0.25,
      },
    ];
    expect(generateYOLOAnnotations(boundingBoxes, imageWidth, imageHeight)).toEqual(expected);
  });
});



describe('generateBoundingBoxesFromYOLO', () => {
  test('should correctly convert YOLO annotations to bounding boxes', () => {
    const annotations: YOLOAnnotation[] = [
      { class_id: 0, x_center: 0.5, y_center: 0.5, width: 1, height: 1},
    ];
    const imageWidth = 640;
    const imageHeight = 480;

    const labels: LabelInfo[] = [
        { label_id: 0, label_name: "Person", label_color: "red" },
        { label_id: 1, label_name: "Car", label_color: "green" },
        { label_id: 2, label_name: "Bicycle", label_color: "blue" },
    ];

    const expected: BoundingBox[] = [
      { x: 0, y: 0, width: 640, height: 480, label_id: 0, color: 'red' },
    ];

    expect(generateBoundingBoxesFromYOLO(annotations, labels, imageWidth, imageHeight)).toEqual(expected);
  });

  test('should correctly convert multiple YOLO annotations to bounding boxes', () => {
    const annotations: YOLOAnnotation[] = [
      { class_id: 0, x_center: 0.5, y_center: 0.5, width: 1, height: 1},
      { class_id: 1, x_center: 0.625, y_center: 0.625, width: 0.25, height: 0.25, },
    ];
    const imageWidth = 640;
    const imageHeight = 480;

    const labels: LabelInfo[] = [
        { label_id: 0, label_name: "Person", label_color: "red" },
        { label_id: 1, label_name: "Car", label_color: "green" },
        { label_id: 2, label_name: "Bicycle", label_color: "blue" },
    ];

    const expected: BoundingBox[] = [
      { x: 0, y: 0, width: 640, height: 480, label_id: 0, color: 'red' },
      { x: 320, y: 240, width: 160, height: 120, label_id: 1, color: 'green' },
    ];

    expect(generateBoundingBoxesFromYOLO(annotations, labels, imageWidth, imageHeight)).toEqual(expected);
  });
});
