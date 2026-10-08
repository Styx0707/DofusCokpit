on(construct){
   while(true)
   {
      if(!(0x31A068BE | 0x31A068BE))
      {
         if(!ord("\x04"))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
      {
         break;
      }
      set("\x16\x18\x14",false);
      contentPath = "none";
      enabled = true;
      set("\x18\f\t",false);
      §§push("styleName");
      §§push("LightBrownWindow");
      if(!ord("\x02"))
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      }
      else
      {
         addr8629:
         set(§§pop(),§§pop());
         title = "";
      }
      return;
   }
   §§goto(addr8629);
}
